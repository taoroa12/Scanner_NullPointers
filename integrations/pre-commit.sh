#!/bin/bash

echo "🔍 [Secret Scanner] Checking your code for vulnerabilities..."

# Run the scanner locally 
python backend/cli.py . --format text --no-color > scan_result.log

# Block commit if CRITICAL or HIGH secrets are found
if grep -q -e "\[CRITICAL\]" -e "\[HIGH\]" scan_result.log; then
    echo "==================================================="
    echo "❌ COMMIT BLOCKED: Secrets found in your code!"
    echo "==================================================="
    cat scan_result.log
    rm scan_result.log
    echo "Please remove the secrets or add the path to .secretignore"
    exit 1
fi

echo "✅ Code is clean. Proceeding with commit."
rm scan_result.log
exit 0