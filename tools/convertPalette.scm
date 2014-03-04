;gimp script
;converts palettes to Gladiator.gpl palette using gimp
;run via: gimp -i -b '(convert-palette "*.tga")' -b '(gimp-quit 0)'
; followed this tutorial: http://www.gimp.org/tutorials/Basic_Batch/

(define (convert-palette pattern)
(let* ((filelist (cadr (file-glob pattern 1))))
	(while (not (null? filelist))
		(let* ((filename (car filelist))
			(image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
			(drawable (car (gimp-image-get-active-layer image))))
		(gimp-image-convert-indexed image 0 4 0 0 0 "Gladiator.gpl")
		(gimp-file-save RUN-NONINTERACTIVE image drawable filename filename)
		(gimp-image-delete image))
	(set! filelist (cdr filelist)))))

;(let* ((filelist (cadr (file-glob pattern 1 ))))
;	(while (not (null? filename (car filelist))
;		(let* ((filename (car filelist))
;			(image (car (gimp-file-load 1 filename filename)))
;			(drawable (car (gimp-image-get-active-layer image))))
;		(gimp-image-convert-indexed 1 image 0 4 0 0 0 "Gladiator.gpl")
;		(gimp-file-save 1 image drawable filename filename)
;		(gimp-image-delete image))
;	(set! filelist (cdr filelist)))))

;	(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
;		(drawable (car (gimp-image-get-active-layer image))))
;	(gimp-image-convert-indexed image 0 4 0 0 0 "Gladiator.gpl")
;	(gimp-file-save RUN-NONINTERACTIVE image drawable filename filename)
;	(gimp-image-delete image)))
