#!/usr/bin/perl

# Check whether there are naming conflicts when names are truncated to
# the DOSish case-ignoring 8.3 format, plus other portability no-nos.

# The "8.3 rule" is loose: "if reducing the directory entry names
# within one directory to lowercase and 8.3-truncated causes
# conflicts, that's a bad thing".  So the rule is NOT the strict
# "no filename shall be longer than eight and a suffix if present
# not longer than three".

my %seen;

sub eight_dot_three {
    next if $seen{$_[0]}++;
    my ($dir, $base, $ext) = ($_[0] =~ m!^(?:(.+)/)?([^/.]+)(?:\.([^/.]+))?$!);
    my $file = $base . ( defined $ext ? ".$ext" : "" );
    $base = substr($base, 0, 8);
    $ext  = substr($ext,  0, 3) if defined $ext;
    if ($dir =~ /\./)  {
	print "directory name contains '.': $dir\n";
    }
    if ($file =~ /[^A-Za-z0-9\._-]/) {
	print "filename contains non-portable characters: $_[0]\n";
    }
    if (length $file > 30) {
	print "filename longer than 30 characters: $_[0]\n"; # make up a limit
    }
    if (defined $dir) {
	return ($dir, defined $ext ? "$dir/$base.$ext" : "$dir/$base");
    } else {
	return ('.', defined $ext ? "$base.$ext" : $base);
    }
}

my %dir;

if (open(MANIFEST, "MANIFEST")) {
    while (<MANIFEST>) {
	chomp;
	s/\s.+//;
	unless (-f) {
	    print "missing: $_\n";
	    next;
	}
	if (tr/././ > 1) {
	    print "more than one dot: $_\n";
	    next;
	}
	while (m!/|\z!g) {
	    my ($dir, $edt) = eight_dot_three($`);
	    ($dir, $edt) = map { lc } ($dir, $edt);
	    push @{$dir{$dir}->{$edt}}, $_;
	}
    }
} else {
    die "$0: MANIFEST: $!\n";
}

for my $dir (sort keys %dir) {
    for my $edt (keys %{$dir{$dir}}) {
	my @files = @{$dir{$dir}->{$edt}};
	if (@files > 1) {
	    print "directory $dir conflict $edt: @files\n";
	}
    }
}
