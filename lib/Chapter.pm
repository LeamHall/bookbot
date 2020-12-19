# name:     Chapter.pm
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Chapter object

package Chapter;
use Moo;

has title     => ( is => 'ro' );
has number    => ( is => 'ro' );
has raw_data  => ( is => 'ro' );
has header    => ( is => 'ro' );


1;

