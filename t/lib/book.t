# name:     book.t
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Tests for Book object.

use strict;
use warnings;
use lib "lib";
use Book;
use Test::More;

my $ns_blurb  = 
"        Academic over-achiever Dede McKenna needs the girl that barely made 
        it into Firster Academy; can their friendship survive bullies, 
        boys, and felonies?
";
my $ns_image  = 'images/navaksen_low.jpg';
my $ns_url    = 'https://www.amazon.com/NavakSen-Firster-Academy-Book-1-ebook/dp/B08SKPNMPH';
my $section_1 = 'Wilbur';
my $section_2 = 'Al';

my $book      = Book->new(
  author      => 'Leam Hall',
  book_dir    => '/home/leam/mybook',
  blurb_file  => 'tmp/navaksen_blurb.txt',
  file_name   => 'al_rides_again',
  image       => 'images/navaksen_low.jpg',
  output_dir  => 'book',
  title       => 'Al rides again',
  url         => $ns_url,
);

$book->add_section( $section_1 );
$book->add_section( $section_2 );

use_ok( 'Book' ) or die $!;
isa_ok( $book, 'Book');

ok( $book->author     eq 'Leam Hall',         'Returns author' );
ok( $book->blurb      eq $ns_blurb,           'Returns book blurb' );
ok( $book->book_dir   eq '/home/leam/mybook', 'Returns output_dir' );
ok( $book->file_name  eq 'al_rides_again',    'Returns book file_name' );
ok( $book->image      eq $ns_image,           'Returns the image location' );
ok( $book->output_dir eq 'book',              'Returns output_dir' );
ok( $book->title      eq 'Al rides again',    'Returns book title' );
ok( $book->url        eq $ns_url,             'Returns URL' );
ok( @{$book->sections} == 2, 'Returns section count' );

done_testing();

