#!/usr/bin/env perl

# name:     bookbot.pl
# version:  0.0.5
# date:     20210104
# author:   Leam Hall
# desc:     Write book from section objects.

## CHANGELOG
# 20210101  Work changes from Section.pm.
# 20210102  Add default config, CLI options, and config file.
# 20210104  Use Book object. Change program to bookbot.pl

use strict;
use warnings;

use Getopt::Long;
use YAML::Tiny;

use lib "lib";
use Book;
use Section;

# subroutines 
sub file_name_from_title {
  (my $file_name)     = @_;
  $file_name          =~ s/[\W]/ /g;
  $file_name          = lc($file_name);
  $file_name          =~ s/\s*$//;
  $file_name          =~ s/\s+/_/g;
  return $file_name;
}

sub show_help {
  print "Usage: $0 \n";
  print "\t --book_dir <dir>       \n";
  print "\t --config_file <file>   \n";
  print "\t --help               This menu \n";
  exit;
}

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

## Set up for GetOptions
my $book_dir;
my $config_file = 'book_config.yml';
my $help;

GetOptions(
  "book_dir=s"    => \$book_dir,
  "config_file=s" => \$config_file,
  "help"          => \$help,
);

show_help() if $help;

# Parse the config file, if there is one.
my %file_configs;
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

# Set the main variables.
my $sections_dir    = "$book_dir/$configs{section_dir}";

# Munge title into a reasonable filename.
$configs{file_name} = file_name_from_title( $configs{title} );

## And away we go!
opendir( my $dir, $sections_dir) or die "Can't open $sections_dir: $!";

my $book = Book->new( 
  author      => $configs{author}, 
  book_dir    => $configs{book_dir},
  file_name   => $configs{file_name},
  output_dir  => $configs{output_dir},
  title       => $configs{title}, 
);

## Build sections and put them into the Book.
# This would be cool for a builder object.
my $section_number = 1;
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
    $book->add_section($section);
    $section_number++;    
  }
} 

close($dir);

$book->write_text; 
