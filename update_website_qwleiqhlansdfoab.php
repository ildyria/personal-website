<?php
$output = shell_exec('git pull -v origin master 2>&1');
echo "<pre>".$output."</pre>";
?>