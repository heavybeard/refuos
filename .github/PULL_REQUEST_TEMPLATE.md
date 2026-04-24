# What does this PR do?

<!-- Short description of the change. -->

## Checklist

### Adding or removing words

- [ ] I edited the right file in `dictionaries/` (one word per line, lowercase, alphabetically sorted)
- [ ] I ran `python3 generate_espanso.py --check` with no errors
- [ ] I ran `python3 generate_espanso.py --output-dir /tmp/refuos-out` and verified the output looks correct
- [ ] There are no duplicates within the file(s) I edited

### Adding a new dictionary

- [ ] I created `dictionaries/<name>.txt` with the word list
- [ ] I added the generation block in `generate_espanso.py`
- [ ] I updated `README.md` to document the new package
- [ ] I ran `python3 generate_espanso.py --check` with no errors

### Other changes (generator, installer, docs)

- [ ] The generator still runs without errors: `python3 generate_espanso.py --check`

## Related issue

Closes #<!-- issue number -->
