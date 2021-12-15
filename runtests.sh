
find . -name "*.pyc" -exec rm {} \;
coverage run -p --source=tests,bot_zakupki -m pytest
# shellcheck disable=SC2181
if [ "$?" = "0" ]; then
    coverage combine
    echo -e "\n======================================================"
    echo "Test Coverage"
    coverage report
    echo -e "\nrun \"coverage html\" for full report"
    echo -e "\n"
fi


