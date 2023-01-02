filename="something.nothing"
for dir in $(ls -d data/copies/*); do touch "$dir/$filename"; done
