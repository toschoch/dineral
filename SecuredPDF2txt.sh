#!/bin/bash

trunk="${1%.pdf}"
echo $trunk
convert -density 300 $1 "$trunk.png"
textfile="$trunk.txt"
touch $textfile
echo ''>$textfile
i=0
for pngfile in $trunk*.png ; do
	i1=$(($i+1))
	echo "read text from page $i1..."
	tesseract $pngfile temp -psm 3 -l deu
	cat $textfile temp.txt > temp
	cat temp > $textfile
	rm temp
	rm temp.txt
done
rm $trunk*.png

