# name:     Report.t
# version:  0.0.1
# date:     20210116
# author:   Leam Hall
# desc:     Generates reports for the Section objects.

## CHANGELOG

use strict;
use warnings;
use lib "lib";
use Report;

use Test::More;

use_ok( 'Report' ) or die $!;

my $data  = "Al looked around; wow! It'd be \"nice\" if he'd joined her.";

my $report  = Report->new (
 string     => $data, 
);
isa_ok( $report, 'Report',            'Initial Report');

ok($report->word_count      == 11,    'Has the right number of words');
ok($report->sentence_count  == 2,     'Has the right number of sentences');
ok($report->grade_level     == 1.57, 'Has the right grade level');
ok($report->syllable_count  == 14,    'Has the right number of syllables');



my %word_list_test = (
  again   => 2,
  al      => 2,
  and     => 1,
  at      => 1,
  happy   => 1,
  he      => 3,
  looked  => 2,
  looking => 1,
  she     => 1,
  there   => 1,
  was     => 3,
);

my $word_list_report = Report->new (
  string  => "Al looked again, and he was there. He was looking at Al, again. She was happy he looked.",
);
 
my %word_list_created = $word_list_report->word_list();
is_deeply( \%word_list_test, \%word_list_created, "Word list hashes are the same" );

my %sorted_word_list_test = (
  3 => ['he', 'was'],
  2 => ['again', 'al', 'looked'],
  1 => ['and', 'at', 'happy', 'looking', 'she', 'there'],
);
my %sorted_word_list_created = $word_list_report->sorted_word_list();
is_deeply( \%sorted_word_list_test, \%sorted_word_list_created, "Sorted word list hashes at the same" );





done_testing();
