#!/bin/bash

trunk="${1%.pdf}"
convert -density 300 $1 "$trunk.png" &> /dev/null
textfile="$trunk.txt"
touch $textfile
echo ''>$textfile
i=0
for pngfile in $trunk*.png ; do
	i1=$(($i+1))
	tesseract $pngfile temp -psm 3 -l deu &> /dev/null
	cat $textfile temp.txt > temp
	cat temp > $textfile
	rm temp
	rm temp.txt
done
rm $trunk*.png

