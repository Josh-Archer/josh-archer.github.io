import os
import re
import unittest
from html.parser import HTMLParser


class SimpleHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.errors = []
        self.ids = set()
        self.hrefs = []
        self.void_tags = {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr"
        }

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if "id" in attr_dict:
            if attr_dict["id"] in self.ids:
                self.errors.append(f"Duplicate id: {attr_dict['id']}")
            self.ids.add(attr_dict["id"])
        if "href" in attr_dict:
            self.hrefs.append(attr_dict["href"])

        if tag.lower() not in self.void_tags:
            self.tags.append(tag.lower())

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.void_tags:
            self.errors.append(f"Void tag {tag} should not have closing tag")
            return
        if not self.tags:
            self.errors.append(f"Unexpected closing tag </{tag}> with no open tags")
            return
        last = self.tags.pop()
        if last != tag_lower:
            self.errors.append(f"Mismatched closing tag </{tag}>, expected </{last}>")


class TestSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.index_path = os.path.join(cls.root_dir, "index.html")
        cls.css_path = os.path.join(cls.root_dir, "style.css")
        cls.readme_path = os.path.join(cls.root_dir, "README.md")

        with open(cls.index_path, "r", encoding="utf-8") as f:
            cls.html = f.read()

        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css = f.read()

        with open(cls.readme_path, "r", encoding="utf-8") as f:
            cls.readme = f.read()

        cls.parser = SimpleHTMLValidator()
        cls.parser.feed(cls.html)

    def test_html_file_exists(self):
        self.assertTrue(os.path.isfile(self.index_path), "index.html must exist (Issue #1)")
        self.assertGreater(len(self.html), 100, "index.html must not be empty")

    def test_html_parses_without_errors(self):
        self.assertEqual(self.parser.errors, [], f"HTML parsing errors found: {self.parser.errors}")
        self.assertEqual(self.parser.tags, [], f"Unclosed tags remaining: {self.parser.tags}")

    def test_doctype_and_lang(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"), "Must declare HTML5 DOCTYPE")
        self.assertIn('<html lang="en">', self.html, "html tag must include lang attribute")

    def test_css_file_exists_and_linked(self):
        self.assertTrue(os.path.isfile(self.css_path), "style.css must exist (Issue #3)")
        self.assertGreater(len(self.css), 500, "style.css must contain styling rules")
        self.assertIn(
            '<link rel="stylesheet" href="style.css">',
            self.html,
            "style.css must be linked in index.html"
        )

    def test_page_sections_exist(self):
        # Issue #2: page sections under the heading
        self.assertIn('id="about"', self.html, "About section must exist (#about)")
        self.assertIn('id="projects"', self.html, "Projects section must exist (#projects)")
        self.assertIn('id="contact"', self.html, "Contact section must exist (#contact)")

    def test_headings_and_landmarks(self):
        self.assertIn("<h1", self.html, "Page must include an h1 heading")
        self.assertIn("<h2", self.html, "Page must include h2 section headings")
        self.assertIn("<header", self.html, "Page must include semantic <header>")
        self.assertIn("<nav", self.html, "Page must include semantic <nav>")
        self.assertIn("<main", self.html, "Page must include semantic <main>")
        self.assertIn("<footer", self.html, "Page must include semantic <footer>")

    def test_skip_link_accessibility(self):
        self.assertIn('class="skip"', self.html, "Accessible skip link must exist")
        self.assertIn('href="#main-content"', self.html, "Skip link must point to #main-content")
        self.assertIn('id="main-content"', self.html, "Main content landmark must have id='main-content'")

    def test_project_list_has_real_public_repos(self):
        # Issue #3: project list with real repo links and descriptions
        expected_repos = [
            "terraform-provider-seerr",
            "homeassistant-addon-muse-gadget",
            "linux-quest",
            "local-swe-agent",
            "agent-meter",
            "terraform-provider-chaptarr",
            "bitwarden-mfa-auth-migrator",
            "unified-ephemeral-runner-broker",
        ]
        for repo in expected_repos:
            repo_link = f"https://github.com/Josh-Archer/{repo}"
            self.assertIn(repo_link, self.html, f"Project list must include link to real repo {repo}")
            self.assertIn(repo, self.html, f"Project card must display repo name {repo}")

    EXCLUDED_REPOS = [
        "snake",
        "8PuzzleAStar",
        "AlumNet",
        "CurrencyConversion",
        "Heisman",
        "GISDirectedStudies",
        "SentenceReadingAgent",
        "Cenith",
        "nlp-hw4",
    ]

    def test_excluded_repos_do_not_appear(self):
        # Repositories deemed unimportant must not appear in project list or site
        for repo in self.EXCLUDED_REPOS:
            repo_link = f"https://github.com/Josh-Archer/{repo}"
            self.assertNotIn(
                repo_link,
                self.html,
                f"Excluded repository link must not appear: {repo_link}",
            )
            self.assertNotIn(
                repo,
                self.html,
                f"Excluded repository name must not appear: {repo}",
            )

    def test_todo_placeholders_present(self):
        # Prompt requirement: do not invent bio details, employers or contact info, leave clearly marked TODO placeholders
        todos = re.findall(r'TODO.*?', self.html, re.IGNORECASE)
        self.assertGreaterEqual(
            len(todos), 2,
            "Must have clearly marked TODO placeholders for bio/employer/contact info"
        )
        self.assertIn("todo-placeholder", self.html, "TODO elements should use placeholder styling")

    def test_internal_anchors_resolve(self):
        for href in self.parser.hrefs:
            if href.startswith("#"):
                anchor = href[1:]
                self.assertIn(
                    anchor,
                    self.parser.ids,
                    f"Anchor {href} references nonexistent ID '{anchor}'"
                )

    def test_local_files_exist(self):
        for href in self.parser.hrefs:
            if not href.startswith("#") and not href.startswith("http://") and not href.startswith("https://"):
                local_file = os.path.join(self.root_dir, href)
                self.assertTrue(os.path.exists(local_file), f"Referenced local file {href} does not exist")

    def test_meta_viewport_and_title(self):
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', self.html)
        self.assertIn("<title>Josh Archer", self.html)


if __name__ == "__main__":
    unittest.main()
