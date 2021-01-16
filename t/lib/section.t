# name:     Section.t
# version:  0.0.4
# date:     20210106
# author:   Leam Hall
# desc:     Tests for the Section object.

## CHANGELOG
# 0.0.2   Moved data parsing into the object.
# 0.0.3   Added test for beginning multple blank lines.
# 0.0.4   Added tests for reports.

use strict;
use warnings;
use lib "lib";
use Section;

use Test::More;

use_ok( 'Section' ) or die $!;

my $section   = Section->new( 
  raw_data    => "[1429.123.0456] Nowhere
  Al looked around. It was interesting.",
  number      => 1,
  has_header  => 1,
);
isa_ok( $section, 'Section', 'Initial section');

my $raw_data = "[1429.123.0456] Nowhere
  Al looked around. It was interesting.";

ok( $section->avg_sentence_length() == 3,     'Returns average sentence length');
ok( $section->avg_word_length()     == 5,     'Returns Average word length');
ok( $section->grade_level()         == 7.21,  'Returns proper grade level');
ok( $section->header()              eq '[1429.123.0456] Nowhere', 'Returns header' );
ok( $section->headless_data()       eq 'Al looked around. It was interesting.', 'Returns headless data');
ok( $section->number()              == 1, 'Returns section number' );
ok( $section->raw_data()            eq $raw_data, 'Returns data');
ok( $section->sentence_count()      == 2, 'Returns sentence count');
ok( $section->word_count()          == 6, 'Returns proper word count');

my $title_section = Section->new(
  raw_data    => "TITLE: An odd event
  [1429.123.0457] Nowhere
  Al looked again, and he was there.",
  has_header  => 1,
);
isa_ok( $title_section, 'Section', 'Title section');
ok( $title_section->header()  eq '[1429.123.0457] Nowhere', 'Title section returns header occuring after TITLE:');
ok( $title_section->title()   eq 'An odd event', 'Title section returns title');
ok( $title_section->avg_sentence_length() == 7, 'TEST Returns average sentence length');

my $headless_section = Section->new(
  raw_data    => "TITLE: Another odd event
  Al looked again, and he was there.",
);
isa_ok( $headless_section, 'Section', 'Headless section');
ok( $headless_section->title()   eq 'Another odd event', 'Headless section returns title');
ok( $headless_section->headless_data() eq 'Al looked again, and he was there.', 'Headless section returns headless_data');
# TODO: Not sure how to check for undef value.
#ok( $headless_section->header() eq undef, 'Headless section returns undef for header()');

my $extra_lines_at_start_section = Section->new(
  raw_data  => "




  [1429.123.0459] Nowhere
  Al was tired, and he looked nice.",
  has_header  => 1,
);
isa_ok( $extra_lines_at_start_section, 'Section', 'Extra lines section');
ok( $extra_lines_at_start_section->header() eq '[1429.123.0459] Nowhere', 'Extra lines still finds header');



done_testing();
