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
