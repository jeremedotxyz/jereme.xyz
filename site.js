document.querySelector('#contact-form')?.addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const body = `Name: ${data.get('name')}\nEmail: ${data.get('email')}\n\n${data.get('message')}`;
  const href = 'mailto:jeremedotxyz@gmail.com?subject=' + encodeURIComponent('Email from jereme.xyz — ' + data.get('topic')) + '&body=' + encodeURIComponent(body);
  const status = document.querySelector('#form-status');
  status.textContent = 'Your draft is ready. ';
  const link = document.createElement('a');
  link.href = href;
  link.textContent = 'Open it again ↗';
  status.append(link);
  window.location.href = href;
});

(() => {
  const header = document.querySelector('.site-header');
  const button = header?.querySelector('.menu-toggle');
  const navigation = header?.querySelector('#main-navigation');
  if (!button || !navigation || header.classList.contains('nav-ready')) return;

  const setOpen = open => {
    if (open) header.dataset.menuOpen = 'true';
    else delete header.dataset.menuOpen;
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };

  button.addEventListener('click', () => setOpen(header.dataset.menuOpen !== 'true'));
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || header.dataset.menuOpen !== 'true') return;
    event.preventDefault();
    setOpen(false);
    button.focus();
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target)) setOpen(false);
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) setOpen(false);
  });
  window.matchMedia('(max-width: 580px)').addEventListener('change', event => {
    const returnFocus = event.matches && navigation.contains(document.activeElement);
    setOpen(false);
    if (returnFocus) button.focus();
  });
  setOpen(false);
  header.classList.add('nav-ready');
})();
