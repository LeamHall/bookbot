#!/usr/bin/env perl

# name:     write_book.pl
# version:  0.0.2
# date:     20210101
# author:   Leam Hall
# desc:     Write book from book and section objects.

## CHANGELOG
# 20210101  Work changes from Section.pm.

use strict;
use warnings;

use lib "lib";
use Book;
use Section;

my $book_dir      = "/home/leam/lang/git/LeamHall/write_book_test";
my $output_dir    = "$book_dir/book";
my $sections_dir  = "$book_dir/sections";
my $book_file     = "$output_dir/NavakSen_new.txt";

my $book  = Book->new(
  title   => "NavakSen",
  author  => "Leam Hall",
);

open( my $file, '>', $book_file) or die "Can't open $book_file: $!";
opendir( my $dir, $sections_dir) or die "Can't open $sections_dir: $!";

select $file;

my $section_number = 1;
my $section_break   = "\n__section_break__\n";

my @files = sort( readdir( $dir ));
foreach my $file (@files) {
  if ( -f "$sections_dir/$file" ) {
    my $raw_data; 
    my $opened  = open( my $fh, '<', "$sections_dir/$file") 
      or die "Can't open $sections_dir/$file: $!";
    if ( $opened ) {
      local $/ = undef;
      $raw_data = <$fh>;
      close($fh);
    }
    my $section = Section->new(
      number      => $section_number,
      raw_data    => $raw_data,
      has_header  => 1,
    );
    $section_number++;    
    print $section_break;
    printf "Chapter %03d", $section->number();
    print "\n\n";
    print $section->header(), "\n\n";
    print $section->headless_data(), "\n\n";
  }
} 

close($dir);
close($file);
 
