#!/usr/bin/env perl

# name:     write_book.pl
# version:  0.0.4
# date:     20210102
# author:   Leam Hall
# desc:     Write book from section objects.

## CHANGELOG
# 20210101  Work changes from Section.pm.
# 20210102  Add default config, CLI options, and config file.

use strict;
use warnings;

use Getopt::Long;
use YAML::Tiny;

use lib "lib";
use Book;
use Section;

### Config precedence:
##  1. Command Line Options
##  2. Config file variables
##  3. Defaults

## Set up defaults
my %configs  = (
  book_dir    => '.',
  output_dir  => 'book',
  report      => 1,
  report_dir  => 'reports',
  section_dir => 'sections',
  title       => "",
);

## Get options from config file
my %file_configs;

## Set up for GetOptions
my $book_dir;
my $config_file = 'book_config.yml';
my $help;

GetOptions(
  "book_dir=s"    => \$book_dir,
  "config_file=s" => \$config_file,
  "help"          => \$help,
);

sub show_help {
  print "Usage: $0 \n";
  print "\t --book_dir <dir>       \n";
  print "\t --config_file <file>   \n";
  print "\t --help               This menu \n";
  exit;
}

show_help() if $help;

# Parse the config file, if there is one.
if ( -f $config_file ) {
  eval {
    %file_configs = %{YAML::Tiny::LoadFile($config_file)};
  }; 
  if ( $@ ) {
    print "Could not parse $config_file, exiting.\n";
    exit;
  }
} else {
  print "No config file found, exiting.\n";
  exit;
}
  
## Merge config file into %config, then CLI.
%configs = ( %configs, %file_configs );
unless ( $book_dir ) {
  $book_dir = $configs{book_dir};
}
if ( ! -d $book_dir ) {
  print "No directory $book_dir. Exiting.\n";
  exit;
}

## Munge title into a reasonable file name.
( my $file_name     = $configs{title} ) =~ s/[\W]/ /g;
$file_name          = lc($file_name);
$file_name          =~ s/\s*$//;
$file_name          =~ s/\s+/_/g;
$file_name          = $file_name . '.txt';

# Set the main variables.
my $output_dir      = "$book_dir/$configs{output_dir}";
my $sections_dir    = "$book_dir/$configs{section_dir}";
my $book_file       = "$output_dir/$file_name";


## TODO: Is the book object needed?
#   Maybe to list pre and post sections, to keep things in order.
#   And to write the different types (text, LaTeX, XML, etc).

## And away we go!
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
 
