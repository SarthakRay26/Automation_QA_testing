/**
 * GitHub Service
 * Handles all GitHub API interactions for creating repos, committing files, 
 * triggering workflows, and fetching workflow status/logs
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class GitHubService {
  constructor() {
    this.token = process.env.GITHUB_TOKEN;
    this.githubUsername = process.env.GITHUB_USERNAME;
    this.apiBase = 'https://api.github.com';
    
    if (!this.token) {
      throw new Error('GITHUB_TOKEN environment variable is required');
    }
    
    if (!this.githubUsername) {
      throw new Error('GITHUB_USERNAME environment variable is required');
    }

    this.headers = {
      'Authorization': `Bearer ${this.token}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json'
    };
  }

  /**
   * Create a new GitHub repository
   * @param {string} repoName - Name of the repository to create
   * @param {boolean} isPrivate - Whether the repo should be private (default: true)
   * @returns {Promise<Object>} Repository creation response
   */
  async createRepo(repoName, isPrivate = true) {
    try {
      const response = await axios.post(
        `${this.apiBase}/user/repos`,
        {
          name: repoName,
          description: 'Automated Selenium test execution repository',
          private: isPrivate,
          auto_init: true // Creates with README to have a default branch
        },
        { headers: this.headers }
      );

      console.log(`✓ Repository created: ${response.data.full_name}`);
      return {
        success: true,
        repo: response.data,
        fullName: response.data.full_name,
        defaultBranch: response.data.default_branch
      };
    } catch (error) {
      if (error.response?.status === 422) {
        // Repository already exists
        console.log(`Repository ${repoName} already exists, using existing repo`);
        return {
          success: true,
          repo: null,
          fullName: `${this.githubUsername}/${repoName}`,
          defaultBranch: 'main',
          alreadyExists: true
        };
      }
      throw this.handleError(error, 'Failed to create repository');
    }
  }

  /**
   * Commit multiple files to a repository
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {Array} files - Array of {path: string, content: string}
   * @param {string} message - Commit message
   * @param {string} branch - Branch name (default: main)
   * @returns {Promise<Object>} Commit response
   */
  async commitFiles(owner, repo, files, message, branch = 'main') {
    try {
      // Step 1: Get the reference to the branch
      const refResponse = await axios.get(
        `${this.apiBase}/repos/${owner}/${repo}/git/ref/heads/${branch}`,
        { headers: this.headers }
      );
      const latestCommitSha = refResponse.data.object.sha;

      // Step 2: Get the tree of the latest commit
      const commitResponse = await axios.get(
        `${this.apiBase}/repos/${owner}/${repo}/git/commits/${latestCommitSha}`,
        { headers: this.headers }
      );
      const baseTreeSha = commitResponse.data.tree.sha;

      // Step 3: Create blobs for each file
      const blobs = await Promise.all(
        files.map(async (file) => {
          const blobResponse = await axios.post(
            `${this.apiBase}/repos/${owner}/${repo}/git/blobs`,
            {
              content: Buffer.from(file.content).toString('base64'),
              encoding: 'base64'
            },
            { headers: this.headers }
          );
          return {
            path: file.path,
            mode: '100644',
            type: 'blob',
            sha: blobResponse.data.sha
          };
        })
      );

      // Step 4: Create a new tree
      const treeResponse = await axios.post(
        `${this.apiBase}/repos/${owner}/${repo}/git/trees`,
        {
          base_tree: baseTreeSha,
          tree: blobs
        },
        { headers: this.headers }
      );

      // Step 5: Create a new commit
      const newCommitResponse = await axios.post(
        `${this.apiBase}/repos/${owner}/${repo}/git/commits`,
        {
          message: message,
          tree: treeResponse.data.sha,
          parents: [latestCommitSha]
        },
        { headers: this.headers }
      );

      // Step 6: Update the reference
      await axios.patch(
        `${this.apiBase}/repos/${owner}/${repo}/git/refs/heads/${branch}`,
        {
          sha: newCommitResponse.data.sha,
          force: false
        },
        { headers: this.headers }
      );

      console.log(`✓ Committed ${files.length} files to ${owner}/${repo}`);
      return {
        success: true,
        commit: newCommitResponse.data,
        commitSha: newCommitResponse.data.sha
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to commit files');
    }
  }

  /**
   * Trigger a workflow_dispatch event
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {string} workflowFileName - Workflow file name (e.g., selenium-test.yml)
   * @param {Object} inputs - Workflow inputs
   * @param {string} ref - Branch/tag/commit ref (default: main)
   * @returns {Promise<Object>} Trigger response
   */
  async triggerWorkflow(owner, repo, workflowFileName, inputs = {}, ref = 'main') {
    try {
      // Wait a bit for files to be available
      await new Promise(resolve => setTimeout(resolve, 2000));

      const response = await axios.post(
        `${this.apiBase}/repos/${owner}/${repo}/actions/workflows/${workflowFileName}/dispatches`,
        {
          ref: ref,
          inputs: inputs
        },
        { headers: this.headers }
      );

      console.log(`✓ Workflow triggered: ${workflowFileName}`);
      
      // Wait for workflow run to appear
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      return {
        success: true,
        message: 'Workflow triggered successfully'
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to trigger workflow');
    }
  }

  /**
   * Get workflow runs for a repository
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {number} limit - Number of runs to fetch
   * @returns {Promise<Object>} Workflow runs response
   */
  async getWorkflowRuns(owner, repo, limit = 10) {
    try {
      const response = await axios.get(
        `${this.apiBase}/repos/${owner}/${repo}/actions/runs`,
        {
          headers: this.headers,
          params: {
            per_page: limit
          }
        }
      );

      return {
        success: true,
        runs: response.data.workflow_runs.map(run => ({
          id: run.id,
          name: run.name,
          status: run.status,
          conclusion: run.conclusion,
          createdAt: run.created_at,
          updatedAt: run.updated_at,
          htmlUrl: run.html_url,
          runNumber: run.run_number
        })),
        totalCount: response.data.total_count
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch workflow runs');
    }
  }

  /**
   * Get specific workflow run by ID
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {number} runId - Workflow run ID
   * @returns {Promise<Object>} Workflow run details
   */
  async getWorkflowRunById(owner, repo, runId) {
    try {
      const response = await axios.get(
        `${this.apiBase}/repos/${owner}/${repo}/actions/runs/${runId}`,
        { headers: this.headers }
      );

      const run = response.data;
      return {
        success: true,
        run: {
          id: run.id,
          name: run.name,
          status: run.status,
          conclusion: run.conclusion,
          createdAt: run.created_at,
          updatedAt: run.updated_at,
          htmlUrl: run.html_url,
          runNumber: run.run_number,
          event: run.event,
          headBranch: run.head_branch
        }
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch workflow run');
    }
  }

  /**
   * Get logs for a specific workflow run
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {number} runId - Workflow run ID
   * @returns {Promise<Object>} Workflow logs
   */
  async getWorkflowLogs(owner, repo, runId) {
    try {
      // Get jobs for the run
      const jobsResponse = await axios.get(
        `${this.apiBase}/repos/${owner}/${repo}/actions/runs/${runId}/jobs`,
        { headers: this.headers }
      );

      const jobs = jobsResponse.data.jobs.map(job => ({
        id: job.id,
        name: job.name,
        status: job.status,
        conclusion: job.conclusion,
        startedAt: job.started_at,
        completedAt: job.completed_at,
        steps: job.steps.map(step => ({
          name: step.name,
          status: step.status,
          conclusion: step.conclusion,
          number: step.number
        }))
      }));

      // Try to get log download URL
      let logUrl = null;
      try {
        const logResponse = await axios.get(
          `${this.apiBase}/repos/${owner}/${repo}/actions/runs/${runId}/logs`,
          {
            headers: this.headers,
            maxRedirects: 0,
            validateStatus: (status) => status === 302
          }
        );
        logUrl = logResponse.headers.location;
      } catch (error) {
        console.log('Log download URL not available yet');
      }

      return {
        success: true,
        jobs: jobs,
        logDownloadUrl: logUrl
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch workflow logs');
    }
  }

  /**
   * Delete a repository
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @returns {Promise<Object>} Deletion response
   */
  async deleteRepo(owner, repo) {
    try {
      await axios.delete(
        `${this.apiBase}/repos/${owner}/${repo}`,
        { headers: this.headers }
      );

      console.log(`✓ Repository deleted: ${owner}/${repo}`);
      return {
        success: true,
        message: 'Repository deleted successfully'
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to delete repository');
    }
  }

  /**
   * Handle API errors
   * @param {Error} error - Error object
   * @param {string} message - Custom error message
   * @returns {Error} Formatted error
   */
  handleError(error, message) {
    console.error(`GitHub API Error: ${message}`);
    
    if (error.response) {
      console.error('Response:', error.response.data);
      return new Error(
        `${message}: ${error.response.data.message || error.response.statusText}`
      );
    }
    
    return new Error(`${message}: ${error.message}`);
  }
}

module.exports = GitHubService;
