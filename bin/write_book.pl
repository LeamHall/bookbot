#!/usr/bin/env perl

# name:     write_book.pl
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Write book from book and chapter objects.

use strict;
use warnings;

use lib "lib";
use Book;
use Chapter;

my $book_dir      = "/home/leam/lang/git/LeamHall/firster_academy_1429_1";
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

my $chapter_number = 1;
my $chapter_break   = "\n__chapter_break__\n";

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
    my $chapter = Chapter->new(
      number => $chapter_number,
      raw_data  => $raw_data,
    );
    $chapter->write_header;
    $chapter->write_headless_data;
    $chapter_number++;    
    print $chapter_break;
    printf "Chapter %03d", $chapter->{number};
    print "\n\n";
    print "$chapter->{header}\n\n";
    print "$chapter->{headless_data}\n\n";
  }
} 

close($dir);
close($file);
 
