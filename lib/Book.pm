# name:     Book.pm
# version:  0.0.2
# date:     20201224
# author:   Leam Hall
# desc:     Book object.

## CHANGELOG
# 0.0.2   Reverted to old style object creation.

use strict;
use warnings;
use lib "lib";

package Book;

sub new {
  my ( $class, %data ) = @_;
  bless {
    _title    => $data{title},
    _author   => $data{author},
    _chapters => [],  
  }, $class;
}

sub author    { $_[0]->{_author}    };
sub title     { $_[0]->{_title}     };
sub chapters  { $_[0]->{_chapters}  };

sub add_chapter {
  my ($self, $chapter) = @_;
  push(@{$self->chapters}, $chapter);
};


1;
