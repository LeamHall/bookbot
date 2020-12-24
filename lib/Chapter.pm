# name:     Chapter.pm
# version:  0.0.2
# date:     20201224
# author:   Leam Hall
# desc:     Chapter object

## CHANGELOG
# 0.0.2   Revert to older OO style. Thank you Damian Conway!

package Chapter;

sub new {
  my ($class, %data) = @_;
  bless {
    _title          => $data{title},
    _raw_data       => $data{raw_data},
    _number         => $data{number},
    _header         => "",
    _headless_data  => "",
  }, $class;
}

sub raw_data  { $_[0]->{_raw_data}  };
sub title     { $_[0]->{_title}     };
sub number    { $_[0]->{_number}    };

sub header    {
  my ($self)  = @_;
  my ($line) = split(/\n/, $self->raw_data() );
  chomp($line);
  $line =~ s/^\s*//;
  $self->{header}  = $line;
}

sub headless_data {
  my ($self)  = @_;
  my $data;
  ($data = $self->raw_data) =~ s/^.*\n//;
  chomp($data);
  $data =~ s/^\s*//;
  $self->{headless_data} = $data; 
}


1;

