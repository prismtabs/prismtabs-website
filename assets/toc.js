/* Table of contents: the mobile "On this page" button and the marker on the section being read. */
(function () {
  var tocToggle = document.getElementById('tocToggle');
  var tocTree = document.getElementById('tocTree');
  if (!tocToggle || !tocTree) return;

  tocToggle.addEventListener('click', function () {
    var expanded = tocToggle.getAttribute('aria-expanded') === 'true';
    tocToggle.setAttribute('aria-expanded', String(!expanded));
  });
  tocTree.addEventListener('click', function (event) {
    if (event.target.closest('a')) tocToggle.setAttribute('aria-expanded', 'false');
  });

  // The current section is the last one whose top has scrolled past the sticky header.
  var tocLinks = Array.prototype.slice.call(tocTree.querySelectorAll('a'));
  var tocSections = tocLinks.map(function (link) {
    return document.getElementById(link.getAttribute('href').slice(1));
  });
  var markCurrentSection = function () {
    var threshold = 140;
    var current = 0;
    tocSections.forEach(function (section, i) {
      if (section && section.getBoundingClientRect().top <= threshold) current = i;
    });
    var atBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
    if (atBottom) current = tocSections.length - 1;
    tocLinks.forEach(function (link, i) {
      if (i === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  var markScheduled = false;
  window.addEventListener('scroll', function () {
    if (markScheduled) return;
    markScheduled = true;
    requestAnimationFrame(function () {
      markScheduled = false;
      markCurrentSection();
    });
  }, { passive: true });
  markCurrentSection();
})();
