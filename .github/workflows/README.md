# GitHub Actions Workflow Guide

This document explains the GitHub Actions workflows used in this repository.

## Workflows

The repository contains the following GitHub Actions workflows:

1. **Update All Stats (Complete Rebuild)** - `update-all.yml`
   - Runs all data generation scripts in a single workflow
   - Manually triggered only
   - Does not trigger other workflows

2. **Update Batting Stats** - `update-batting.yml`
   - Updates batting statistics and trends
   - Schedule: Daily at 12:00 UTC
   - Can be manually triggered

3. **Update Pitching Stats** - `update-pitching.yml`
   - Updates pitching statistics and trends
   - Schedule: Every Monday at 03:00 UTC
   - Can be manually triggered

4. **Update Standings** - `update-standings.yml`
   - Updates team standings and division charts
   - Schedule: Daily at 13:00 UTC
   - Can be manually triggered

5. **Update MVP and Cy Young Predictions** - `update-mvp-cy-young.yml`
   - Updates award predictions
   - Schedule: Daily at 14:00 UTC
   - Can be manually triggered

6. **Update Prediction Tracking** - `update-prediction-tracking.yml`
   - Archives prediction history
   - Schedule: Daily at 14:30 UTC
   - Can be manually triggered

7. **Update Playoff Predictions** - `update-playoffs.yml`
   - Updates playoff predictions
   - Schedule: Daily at 13:30 UTC
   - Can be manually triggered

## Important Notes

- All workflows contain a `workflow_dispatch` trigger to enable manual runs
- The `workflow_dispatch` trigger uses the minimalist syntax `workflow_dispatch: {}`
- Workflows check the branch and only run scheduled updates on the main branch
- The update-all.yml workflow does not trigger other workflows; it runs all scripts directly

## Troubleshooting

If you encounter issues with workflow dispatch:

1. Verify that all workflow files have a valid `workflow_dispatch` trigger
2. Check if there are any hidden characters or BOM markers in the YAML files
3. Run the validation script at `scripts/validate_workflows.sh`
4. Use the GitHub UI to manually trigger workflows rather than API calls

## Last Updated

This guide was last updated on July 14, 2025.