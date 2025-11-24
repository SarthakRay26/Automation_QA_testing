/**
 * Test Run Controller
 * Handles HTTP requests for creating and managing GitHub Actions test runs
 */

const GitHubService = require('../services/githubService');
const fs = require('fs');
const path = require('path');

class TestRunController {
  constructor() {
    this.githubService = new GitHubService();
    this.activeRuns = new Map(); // Store run metadata in memory
  }

  /**
   * Create a new test run
   * POST /api/create-test-run
   * Body: { testScript: string, testName?: string, repoName?: string }
   */
  async createTestRun(req, res) {
    try {
      const { testScript, testName = 'selenium-test', repoName } = req.body;

      // Validate input
      if (!testScript || typeof testScript !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'testScript is required and must be a string'
        });
      }

      const timestamp = Date.now();
      const runId = `test-run-${timestamp}`;
      const finalRepoName = repoName || `selenium-test-${timestamp}`;

      console.log(`\n🚀 Creating test run: ${runId}`);
      console.log(`📦 Repository: ${finalRepoName}`);

      // Step 1: Create repository
      const repoResult = await this.githubService.createRepo(finalRepoName, true);
      const [owner, repo] = repoResult.fullName.split('/');

      // Step 2: Load workflow template
      const workflowPath = path.join(__dirname, '../config/workflow-template.yml');
      const workflowContent = fs.readFileSync(workflowPath, 'utf-8');

      // Step 3: Prepare files to commit
      const files = [
        {
          path: 'test_script.py',
          content: testScript
        },
        {
          path: '.github/workflows/selenium-test.yml',
          content: workflowContent
        }
      ];

      // Step 4: Commit files
      await this.githubService.commitFiles(
        owner,
        repo,
        files,
        `Add Selenium test script for run ${runId}`,
        'main'
      );

      // Step 5: Trigger workflow
      await this.githubService.triggerWorkflow(
        owner,
        repo,
        'selenium-test.yml',
        { test_id: runId },
        'main'
      );

      // Step 6: Get the workflow run ID
      const runsResult = await this.githubService.getWorkflowRuns(owner, repo, 1);
      const latestRun = runsResult.runs[0];

      // Store run metadata
      const runMetadata = {
        runId,
        owner,
        repo,
        repoFullName: repoResult.fullName,
        workflowRunId: latestRun?.id,
        testName,
        createdAt: new Date().toISOString(),
        status: 'queued'
      };
      this.activeRuns.set(runId, runMetadata);

      console.log(`✅ Test run created successfully`);

      return res.status(201).json({
        success: true,
        data: {
          runId,
          workflowRunId: latestRun?.id,
          repository: repoResult.fullName,
          repoUrl: `https://github.com/${repoResult.fullName}`,
          workflowUrl: latestRun?.htmlUrl,
          status: 'queued',
          message: 'Test run created and workflow triggered successfully'
        }
      });

    } catch (error) {
      console.error('Error creating test run:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to create test run'
      });
    }
  }

  /**
   * Get test run status
   * GET /api/status/:runId
   */
  async getStatus(req, res) {
    try {
      const { runId } = req.params;

      // Get run metadata
      const metadata = this.activeRuns.get(runId);
      if (!metadata) {
        return res.status(404).json({
          success: false,
          error: 'Test run not found'
        });
      }

      const { owner, repo, workflowRunId } = metadata;

      // Fetch current workflow status from GitHub
      const runResult = await this.githubService.getWorkflowRunById(
        owner,
        repo,
        workflowRunId
      );

      const status = runResult.run.status;
      const conclusion = runResult.run.conclusion;

      // Update stored metadata
      metadata.status = status;
      metadata.conclusion = conclusion;
      metadata.updatedAt = new Date().toISOString();
      this.activeRuns.set(runId, metadata);

      return res.status(200).json({
        success: true,
        data: {
          runId,
          workflowRunId,
          status,
          conclusion,
          workflowUrl: runResult.run.htmlUrl,
          createdAt: metadata.createdAt,
          updatedAt: metadata.updatedAt
        }
      });

    } catch (error) {
      console.error('Error fetching status:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to fetch test run status'
      });
    }
  }

  /**
   * Get test run logs
   * GET /api/logs/:runId
   */
  async getLogs(req, res) {
    try {
      const { runId } = req.params;

      // Get run metadata
      const metadata = this.activeRuns.get(runId);
      if (!metadata) {
        return res.status(404).json({
          success: false,
          error: 'Test run not found'
        });
      }

      const { owner, repo, workflowRunId } = metadata;

      // Fetch logs from GitHub
      const logsResult = await this.githubService.getWorkflowLogs(
        owner,
        repo,
        workflowRunId
      );

      return res.status(200).json({
        success: true,
        data: {
          runId,
          workflowRunId,
          jobs: logsResult.jobs,
          logDownloadUrl: logsResult.logDownloadUrl,
          workflowUrl: `https://github.com/${owner}/${repo}/actions/runs/${workflowRunId}`
        }
      });

    } catch (error) {
      console.error('Error fetching logs:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to fetch test run logs'
      });
    }
  }

  /**
   * Get test run artifacts
   * GET /api/artifacts/:runId
   */
  async getArtifacts(req, res) {
    try {
      const { runId } = req.params;

      // Get run metadata
      const metadata = this.activeRuns.get(runId);
      if (!metadata) {
        return res.status(404).json({
          success: false,
          error: 'Test run not found'
        });
      }

      const { owner, repo, workflowRunId } = metadata;

      // Fetch artifacts from GitHub
      const artifactsResult = await this.githubService.getWorkflowArtifacts(
        owner,
        repo,
        workflowRunId
      );

      return res.status(200).json({
        success: true,
        data: {
          runId,
          workflowRunId,
          artifacts: artifactsResult.artifacts,
          repoUrl: `https://github.com/${owner}/${repo}`
        }
      });

    } catch (error) {
      console.error('Error fetching artifacts:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to fetch artifacts'
      });
    }
  }

  /**
   * List all test runs
   * GET /api/runs
   */
  async listRuns(req, res) {
    try {
      const runs = Array.from(this.activeRuns.values()).map(run => ({
        runId: run.runId,
        workflowRunId: run.workflowRunId,
        repository: run.repoFullName,
        status: run.status,
        conclusion: run.conclusion,
        createdAt: run.createdAt,
        updatedAt: run.updatedAt
      }));

      return res.status(200).json({
        success: true,
        data: {
          runs,
          count: runs.length
        }
      });

    } catch (error) {
      console.error('Error listing runs:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to list test runs'
      });
    }
  }

  /**
   * Delete a test run and its repository
   * DELETE /api/runs/:runId
   */
  async deleteRun(req, res) {
    try {
      const { runId } = req.params;

      // Get run metadata
      const metadata = this.activeRuns.get(runId);
      if (!metadata) {
        return res.status(404).json({
          success: false,
          error: 'Test run not found'
        });
      }

      const { owner, repo } = metadata;

      // Delete repository
      await this.githubService.deleteRepo(owner, repo);

      // Remove from active runs
      this.activeRuns.delete(runId);

      return res.status(200).json({
        success: true,
        message: 'Test run and repository deleted successfully'
      });

    } catch (error) {
      console.error('Error deleting run:', error);
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to delete test run'
      });
    }
  }
}

module.exports = TestRunController;
