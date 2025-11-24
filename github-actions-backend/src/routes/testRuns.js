/**
 * Test Run Routes
 * Defines API endpoints for managing test runs
 */

const express = require('express');
const router = express.Router();
const TestRunController = require('../controllers/testRunController');

// Initialize controller
const controller = new TestRunController();

/**
 * @route   POST /api/create-test-run
 * @desc    Create a new test run with GitHub Actions
 * @body    { testScript: string, testName?: string, repoName?: string }
 * @returns { runId, workflowRunId, repository, status }
 */
router.post('/create-test-run', (req, res) => {
  controller.createTestRun(req, res);
});

/**
 * @route   GET /api/status/:runId
 * @desc    Get status of a test run
 * @param   runId - Test run identifier
 * @returns { runId, status, conclusion, workflowUrl }
 */
router.get('/status/:runId', (req, res) => {
  controller.getStatus(req, res);
});

/**
 * @route   GET /api/logs/:runId
 * @desc    Get logs for a test run
 * @param   runId - Test run identifier
 * @returns { jobs, logDownloadUrl, workflowUrl }
 */
router.get('/logs/:runId', (req, res) => {
  controller.getLogs(req, res);
});

/**
 * @route   GET /api/runs
 * @desc    List all test runs
 * @returns { runs: Array, count: number }
 */
router.get('/runs', (req, res) => {
  controller.listRuns(req, res);
});

/**
 * @route   DELETE /api/runs/:runId
 * @desc    Delete a test run and its repository
 * @param   runId - Test run identifier
 * @returns { success, message }
 */
router.delete('/runs/:runId', (req, res) => {
  controller.deleteRun(req, res);
});

module.exports = router;
