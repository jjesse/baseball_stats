#!/bin/bash
# Make workflow validation scripts executable
chmod +x /home/jjesse/github/baseball_stats/scripts/validate_workflows.sh
chmod +x /home/jjesse/github/baseball_stats/scripts/test_workflow_dispatch.sh

echo "Made workflow validation scripts executable."
echo "You can now run:"
echo "  ./scripts/validate_workflows.sh"
echo "  ./scripts/test_workflow_dispatch.sh"