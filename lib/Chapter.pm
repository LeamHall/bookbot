# name:     Chapter.pm
# version:  0.0.1
# date:     20201219
# author:   Leam Hall
# desc:     Chapter object

package Chapter;
use Moo;

has title         => ( is => 'ro' );
has number        => ( is => 'ro' );
has raw_data      => ( is => 'ro' );
has header        => ( is => 'rw' );
has headless_data => ( is => 'rw' );

sub write_header {
  my ($self)  = @_;
  my ($line) = split(/\n/, $self->raw_data() );
  chomp($line);
  $line =~ s/^\s*//;
  $self->{header}  = $line;
}

sub write_headless_data {
  my ($self)  = @_;
  my $data;
  ($data = $self->raw_data) =~ s/^.*\n//;
  chomp($data);
  $data =~ s/^\s*//;
  $self->{headless_data} = $data; 
}


1;

