#!/bin/bash

targets="main admin print 500"

dir=$(dirname $0)/..
mkdir -p $dir/css/
for target in $targets
do
    recess --compile --compress $dir/less/$target.less > $dir/css/$target.css
done
