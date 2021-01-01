package Book;

use 5.006;
use strict;
use warnings;

=head1 NAME

Book

=head1 VERSION

Version 0.03

=cut

our $VERSION = '0.03';


=head1 SYNOPSIS

Book object


    use Book;

    my $book    = Book->new(
      title     => 'Al resuces the universe again',
      author    => 'Leam Hall',
    );


=head1 SUBROUTINES/METHODS

=head2 new

Initializes with a data hash consisiting of title and author.
  
=cut

sub new {
  my ( $class, %data ) = @_;
  bless {
    _title    => $data{title},
    _author   => $data{author},
    _sections => [],  
  }, $class;
}

=head2 add_section

Appends a section object to the internal list of sections.

=cut

sub add_section {
  my ($self, $section) = @_;
  push(@{$self->sections}, $section);
};


=head2 author

Returns the author.

=cut

sub author    { $_[0]->{_author}    };

=head2 title

Returns the title.

=cut

sub title     { $_[0]->{_title}     };


=head2 sections

Returns the array of section objects.

=cut

sub sections  { $_[0]->{_sections}  };


=head1 AUTHOR

Leam Hall, C<< <leamhall at gmail.com> >>

=head1 BUGS

Please report any bugs or feature requests to L<https://github.com/LeamHall/bookbot/issues>.




=head1 SUPPORT

You can find documentation for this module with the perldoc command.

    perldoc Book


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

1; # End of Book
