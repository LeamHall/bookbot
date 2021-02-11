#!/usr/bin/env perl

# name:     make_thumbnail.pl
# version:  0.0.2
# date:     20201121
# author:   Leam Hall
# desc:     Make thumbnail images.

# Notes
#   Requires Imager::Transformations
#   My standard web image 'file' details are:
#     JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, 
#     segment length 16, baseline, precision 8, 540x810, components 3
#   Each format has an Imager::File::<FORMAT> module required.

# Reading
#   http://imager.perl.org/docs/Imager/Transformations.html

# TODO
#   Specify format output
#   Specify scale factor
#   Specify xpixels and ypixels

use strict;
use warnings;

use Getopt::Long;
use Imager;

my $file;
my $xpixels     = 540;  # xpixels are width
my $ypixels     = 810;  # ypixels are height
my $scalefactor = .3;   # If xpixels or ypixels not supplied. Default is .5

GetOptions (
  "file=s"    => \$file,
);

( $file ) or die "Need file to process";

my $img   = Imager->new(file=>$file);

$file =~ s/\.[^.]*$//;

my $thumb   = $img->scale(xpixels => $xpixels, ypixels => $ypixels);
$thumb->filter(type=>'autolevels');

SAVE:
for my $format ( qw( jpeg gif png tiff ppm )) {
  if ($Imager::formats{$format}) {
    $file .= "_low.$format";
    print "Storing image as $file.\n";
    $thumb->write(file=>$file) or die $thumb->errstr;
    last SAVE;
  }
}


