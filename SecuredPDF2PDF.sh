parallel "tesseract {} {} -l deu hocr; hocr2pdf -i {} -n -o {}.pdf < {}.html" ::: *.png
