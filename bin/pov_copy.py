import argparse
import os
import shutil


def parse_pov_list(filepath):
    pov_data = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            filename = parts[0]
            characters = parts[1:]
            pov_data[filename] = characters
    return pov_data


def find_chapters_for_character(pov_data, character):
    chapters = [
        filename
        for filename, characters in pov_data.items()
        if character in characters
    ]
    return sorted(chapters)


def copy_chapters(filenames, source_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for filename in filenames:
        src = os.path.join(source_dir, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser(
        description="Copy chapters featuring a specific character to a new directory."
    )
    parser.add_argument("character", help="Character first name (e.g. rachela)")
    parser.add_argument("--pov-list", default="research/pov_list.txt",
                        help="Path to pov_list.txt (default: research/pov_list.txt)")
    parser.add_argument("--source-dir", default="chapters",
                        help="Directory containing chapter files (default: chapters)")
    parser.add_argument("--dest-dir",
                        help="Destination directory (default: <character>_chapters)")
    args = parser.parse_args()

    dest_dir = args.dest_dir or f"{args.character}_chapters"

    pov_data = parse_pov_list(args.pov_list)
    chapters = find_chapters_for_character(pov_data, args.character)

    if not chapters:
        print(f"No chapters found for character: {args.character}")
        return

    copy_chapters(chapters, args.source_dir, dest_dir)
    print(f"Copied {len(chapters)} chapters for '{args.character}' to {dest_dir}/")
    for ch in chapters:
        print(f"  {ch}")


if __name__ == "__main__":
    main()
