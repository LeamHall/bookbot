# name:     Chapter.t
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Tests for the Chapter object.

use strict;
use warnings;
use lib "lib";
use Chapter;

use Test::More;

use_ok( 'Chapter' ) or die $!;

my $chapter = Chapter->new( 
  raw_data  => 'Al looked around. It was interesting.',
  header    => '[1429.123.0456]',
  number    => 1,
  title     => 'The Chapter',
);
isa_ok( $chapter, 'Chapter');

ok( $chapter->raw_data()  eq 'Al looked around. It was interesting.', 'Returns data');
ok( $chapter->header()    eq '[1429.123.0456]', 'Returns header' );
ok( $chapter->number()    == 1, 'Returns chapter number' );
ok( $chapter->title()     eq 'The Chapter', 'Returns title' );

done_testing();

