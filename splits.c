/*

		  Split a file into multiple chunks

			    by John Walker
		       http://www.fourmilab.ch/

		This program is in the public domain.

	This  program  reads  a  file  given by its first argument (or
        standard input if the argument is "-") and writes files in the
	current  directory  of	the  size given by the second argument
	(default 100K).  These files are named with the  name  of  the
        input  file ("StdIn" if "-" was used) with a three digit chunk
	number appended.  You can reassemble the  original  file  with
	the command:

	    cat <fname>.??? ><fname>

	or the equivalent COPY /B on MSDOS.

	This program assumes that fread() and  fwrite()  take  4  byte
	block  length arguments and can read and write chunks as large
	as the	given  specified  output  block  size.	 Thus,	it  is
	unlikely to work on 16 bit architectures.  File open calls may
	have to be modified on systems	where  binary  files  must  be
	identified at open time.

	Release history:

	    April 12, 1993:	Original release.
	    October 26, 1998:	HTML documentation, WIN32 binary file
				support and executable program, switch
				to ZIP distribution format.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

int main(int argc, char *argv[])
{
    char splitfn[280];
    long part = 0, chunk = 100 * 1024;
    FILE *fp, *op;
    char *fb;
    char *ofn = "StdIn";

    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: splits [<filename>|-] [chunk(Kb)]\n");
	return 2;
    }

    if (argc > 2) {
	long lch = atol(argv[2]);

	if (lch < 1) {
            fprintf(stderr, "Invalid chunk size.\n");
	    return 2;
	}
	chunk = lch * 1024L;
    }

    fb = malloc((unsigned) chunk);
    if (fb == NULL) {
        fprintf(stderr, "Unable to allocate %ld byte I/O buffer.\n", chunk);
	return 1;
    }
    if (strcmp(argv[1], "-") != 0) {
	ofn = argv[1];
        fp = fopen(argv[1], "rb");
	if (fp == NULL) {
            fprintf(stderr, "Cannot open file %s\n", argv[1]);
	    return 2;
	}
    } else {

	/*  Warning!  Splits needs to read its input file and
	    write the output files in binary mode--without any
	    translation of end of line or end of file sequences.
	    On Unix, there is no distinction between text and
	    binary I/O, but on ill-conceived systems such as
	    MS-DOS/Windows and Mac OS, the default I/O mode
	    for C programs is text mode.  Complicating the
	    matter further is the fact that, while almost all
            modern implementations of C allow a "b" specification
            in an fopen() call (on Unix it's just ignored), there
	    is no standard whatsoever for setting the mode of
	    automatically-opened streams such as stdin and
	    stdout.

	    This file contains code, conditional on _WIN32, which
	    sets binary mode using the method prescribed by
            Microsoft Visual C 5.0 ("Monkey C"); this may
            require modification if you're using a different
	    compiler or release of Monkey C.  When opening files
            explicitly, we also specify the "b" modifier so that
            even if standard input doesn't work, reading explicitly
	    named files will still work.  */

	fp = stdin;
#ifdef _WIN32
	_setmode(_fileno(fp), _O_BINARY);
#endif
    }

    while (1) {
	long fl;

	fl = fread(fb, 1, (int) chunk, fp);
	if (fl > 0) {
            sprintf(splitfn, "%03ld.%s", ++part, ofn);
            op = fopen(splitfn, "wb");
	    if (op == NULL) {
                fprintf(stderr, "Cannot create output file %s\n", splitfn);
		return 2;
	    }
	    fwrite(fb, 1, (int) fl, op);
	    fclose(op);
	} else {
	    break;
	}
    }

    if (fp != stdin) {
	fclose(fp);
    }
    return 0;
}
