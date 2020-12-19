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

use_ok( 'Book' ) or die $!;

my $book    = Book->new(
  title     => 'Al rides again',
  author    => 'Leam Hall',
);
isa_ok( $book, 'Book');

ok( $book->author eq 'Leam Hall',       'Returns author' );
ok( $book->title  eq 'Al rides again',  'Returns book title' );

my $chapter_1 = 'Wilbur';
my $chapter_2 = 'Al';
$book->add_chapter( $chapter_1 );
$book->add_chapter( $chapter_2 );
ok( @{$book->chapters} == 2, 'Returns chapter count' );
done_testing();

