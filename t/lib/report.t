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

print "grade level is ", $report->grade_level, ".\n";
done_testing();
