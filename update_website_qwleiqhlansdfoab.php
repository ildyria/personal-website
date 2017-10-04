<?php
$output = shell_exec('git pull -v origin master 2>&1');
echo "<pre>".$output."</pre>";
$output = shell_exec('./build.py 2>&1');
echo "<pre>".$output."</pre>";
?>
