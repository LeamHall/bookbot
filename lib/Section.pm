package Section;

use 5.006;
use strict;
use warnings;

=head1 NAME

Section

=head1 VERSION

Version 0.03

=cut

our $VERSION = '0.03';


=head1 SYNOPSIS

Section Object

    use Section;

    my $section = Section->new(
      raw_data    => "TITLE: An odd event
      [1429.123.0457] Nowhere
      Al looked again, and he was there.",
      has_header  => 1,
      number      => 1,
    );

=head1 SUBROUTINES/METHODS

=head2 new

new takes a hash of data, to include: the section number ('number') if relevant,
and the raw_data from the file.

It uses the raw_data, and a "has_header" flag to create the section header.

The section's title is set by the first data line beginning with "TITLE:".

=cut

sub new {
  my ($class, %data) = @_;
  my $self = {
    _has_header     => $data{has_header} || 0,
    _header         => undef,
    _headless_data  => undef,
    _number         => $data{number},
    _raw_data       => $data{raw_data},
    _report         => undef,
    _title          => undef,
  };
  bless $self, $class;
  #$self->_write_report();
}

=head2 avg_word_length

Returns the average word length.

=cut

sub avg_word_length {
  my ( $self ) = @_;
  return $self->{_report}->avg_word_length;
}

=head2 header

Returns the section header, if appropriate, or undef.

=cut

sub header {
  my ($self)  = @_;
  return undef unless $self->{_has_header};
  my (@lines) = split(/\n/, $self->raw_data() );
  foreach my $line (@lines) {
    next if $line =~ m/TITLE:/;
    chomp($line);
    $line =~ s/^\s*//;
    next unless length($line);  # Skips extra blank lines at start.
    $self->{_header}  = $line;
    last;
  }
  return $self->{_header};
}

=head2 headless_data

Returns the raw_data, minus any header or title.

=cut

sub headless_data {
  my ($self)  = @_;
  my $data;
  ($data = $self->raw_data) =~ s/^TITLE:.*\n//;
  # TODO: Not sure this covers multiple empty blank lines.
  $data =~ s/^.*\n// if $self->{_has_header};
  $data =~ s/^\s*//;
  chomp($data);
  $self->{_headless_data} = $data; 
  return $self->{_headless_data};
}

=head2 kinkaid

Retuns the Kinkaid score per: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests

=cut

sub kincaid {
  my ($self)  = @_;
  my $k = sprintf("%0.2f", $self->{_report}->kincaid);
  return $k;
}

  
=head2 number

Returns the section number.

=cut

sub number    { $_[0]->{_number}    };


=head2 raw_data 

Returns the raw_data from the file.

=cut

sub raw_data  { $_[0]->{_raw_data}  };

=head2 title

Returns the title.

=cut

sub title { 
  my ($self)  = @_;
  my (@lines) = split(/\n/, $self->raw_data() );
  foreach my $line (@lines) {
    if ( $line =~ m/TITLE:/ ) {
      chomp($line);
      $line =~ s/^\s*TITLE:\s*//;
      $self->{_title}  = $line;
      last;
    }
  }
  return $self->{_title};
}

=head2 word_count

Returns the word count of the section, minus title or header.

=cut

sub word_count {
  my ($self)  = @_;
  return $self->{_report}->num_words;  
}


=head2 _write_report

Writes the report data.

=cut

sub _write_report {
  my ($self)  = @_;
  use Text::IQ::EN;
  my $text = $self->headless_data;
  $self->{_report} = Text::IQ::EN->new( \$text );
}



=head1 AUTHOR

Leam Hall, C<< <leamhall at gmail.com> >>

=head1 BUGS

Please report any bugs or feature requests to L<https://github.com/LeamHall/bookbot/issues>.  




=head1 SUPPORT

You can find documentation for this module with the perldoc command.

    perldoc Section


You can also look for information at:

=over 4

=item * GitHub Project Page

L<https://github.com/LeamHall/bookbot>

=item * CPAN Ratings

L<https://cpanratings.perl.org/d/.>

=item * Search CPAN

L<https://metacpan.org/release/.>

=back


=head1 ACKNOWLEDGEMENTS

Besides Larry Wall, you can blame the folks on Freenode#perl for this stuff existing.


=head1 LICENSE AND COPYRIGHT

This software is Copyright (c) 2021 by Leam Hall.

This is free software, licensed under:

  The Artistic License 2.0 (GPL Compatible)


=cut

1; # End of Section
