# name:     Book.pm
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Book object.

use strict;
use warnings;
use lib "lib";

package Book;
use Moo;

has title     => ( is => 'ro' );
has author    => ( is => 'ro' );
has chapters  => ( is => 'rw', default => sub { [] } ); 

sub add_chapter {
  my ($self, $chapter) = @_;
  push(@{$self->chapters}, $chapter);
};


1;
