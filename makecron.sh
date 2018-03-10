{ crontab -l; echo "* * * * * cd $(pwd) && ./task.py >> tasklog.log 2>&1"; } | crontab - ;
