#!/bin/bash

for file in $1/Januar.pdf ; do
	echo "process $file..."
	filestripped="$2/${file%.pdf}"
 	convert -density 300 $file "${filestripped}.png"
	textfile="${filestripped}.txt"
	touch $textfile
	echo ''>$textfile
	i=0
	for pngfile in $2/${filestripped}*.png ; do
		i=$(($i+1))
		echo "read text from page $i..."
		tesseract $pngfile ${pngfile%.png} -psm 3 -l deu
		temptextfile="${pngfile%.png}.txt"
		cat $textfile $temptextfile > temp
		cat temp > $textfile
		rm temp
		rm $temptextfile
		rm $pngfile
	echo "write $textfile..."
	done
done	
