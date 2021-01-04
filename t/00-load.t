#!perl
use 5.006;
use strict;
use warnings;
use Test::More;

plan tests => 2;

BEGIN {
    use_ok( 'Book' ) || print "Bail out!\n";
    use_ok( 'Section' ) || print "Bail out!\n";
}

diag( "Testing Book $Book::VERSION, Perl $], $^X" );
