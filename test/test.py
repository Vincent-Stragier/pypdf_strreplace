"""Tests for pypdf_strreplace.py."""

import subprocess

from pathlib import Path

import pytest


def gm(*args, **kwargs):
    """Run a GraphicsMagick command and return the completed process."""
    return subprocess.run(
        ["gm", *args], check=True, capture_output=True, text=True, **kwargs
    )


@pytest.mark.parametrize(
    "name,pdf,search,replace",
    [
        ("inkscape_simple", "Inkscape", "Inkscape 1.1.2", "pleasure"),
        ("libreoffice_simple", "LibreOffice", "7.3.2", "infinite"),
        ("dmytryo_simple", "Dmytro", "PDF", "DOC"),
        ("xelatex_simple", "xelatex", "symbol", "character"),
        ("inkscape_multiple_operands", "Inkscape", "created", "made"),
        ("xelatex_multiple_operations", "xelatex", "n α symbo", "ny content unti"),
        ("libreoffice_multiple_operations",
         "LibreOffice", "PDF file", "text document"),
        ("dmytryo_multiple_occurrences", "Dmytro", "text", "fuzz"),
        ("dmytryo_needle_remains", "Dmytro", "text", "context"),
    ],
)
def test_pdf_rewrite(name, pdf, search, replace, tmp_path: Path):
    """Test that pypdf_strreplace.py correctly rewrites PDFs."""
    output = tmp_path / "output.pdf"
    reference_tiff = tmp_path / "reference.tiff"
    output_tiff = tmp_path / "output.tiff"
    command = [
        "timeout",
        "--verbose",
        "3",
        "python",
        "pypdf_strreplace.py",
        f"pdfs/{pdf}.pdf",
        "--output",
        str(output),
        "--search",
        search,
        "--replace",
        replace,
    ]

    # Run the script under test
    subprocess.run(
        command,
        check=True,
    )

    # Render expected and actual
    gm(
        "convert",
        "-background",
        "white",
        "-extent",
        "0x0",
        "-density",
        "150",
        "+matte",
        f"test/{name}.pdf",
        str(reference_tiff),
    )

    gm(
        "convert",
        "-background",
        "white",
        "-extent",
        "0x0",
        "-density",
        "150",
        "+matte",
        str(output),
        str(output_tiff),
    )

    # Compare page by page
    pages = gm("identify", str(output_tiff)).stdout.strip().splitlines()
    pages_count = len(pages)

    for page_index in range(pages_count):
        try:
            gm(
                "compare",
                f"{reference_tiff}[{page_index}]",
                f"{output_tiff}[{page_index}]",
                "-metric",
                "PAE",
                "-maximum-error",
                "0",
            )
        except subprocess.CalledProcessError as exc:
            pytest.fail(f"Page {page_index} mismatch:\n{exc.stderr}")
