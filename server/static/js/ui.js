(function () {
  const body = document.body;

  function closeDropdowns() {
    document.querySelectorAll('.dropdown.open').forEach((dropdown) => {
      dropdown.classList.remove('open');
      const button = dropdown.querySelector('[data-dropdown-toggle]');
      if (button) {
        button.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function closeMenus() {
    document.querySelectorAll('.navbar-menu.open').forEach((menu) => {
      menu.classList.remove('open');
      const toggle = document.querySelector(`[data-menu-target="${menu.id}"]`);
      if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Открыть меню');
      }
    });
  }

  function showModal(target) {
    const modal = typeof target === 'string' ? document.getElementById(target) : target;
    if (!modal) {
      return;
    }
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    body.style.overflow = 'hidden';
    document.dispatchEvent(new CustomEvent('paui:modal-open', { detail: { modalId: modal.id } }));
  }

  function hideModal(target) {
    const modal = typeof target === 'string' ? document.getElementById(target) : target;
    if (!modal) {
      return;
    }
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    if (!document.querySelector('.modal.show')) {
      body.style.overflow = '';
    }
    document.dispatchEvent(new CustomEvent('paui:modal-close', { detail: { modalId: modal.id } }));
  }

  window.PAUI = {
    showModal,
    hideModal,
  };

  document.addEventListener('click', (event) => {
    const menuToggle = event.target.closest('[data-menu-toggle]');
    if (menuToggle) {
      const menu = document.getElementById(menuToggle.getAttribute('data-menu-target'));
      if (!menu) {
        return;
      }

      const willOpen = !menu.classList.contains('open');
      closeMenus();
      menu.classList.toggle('open', willOpen);
      menuToggle.setAttribute('aria-expanded', String(willOpen));
      menuToggle.setAttribute('aria-label', willOpen ? 'Закрыть меню' : 'Открыть меню');
      return;
    }

    const dropdownToggle = event.target.closest('[data-dropdown-toggle]');
    if (dropdownToggle) {
      const dropdown = dropdownToggle.closest('.dropdown');
      const willOpen = !dropdown.classList.contains('open');
      closeDropdowns();
      dropdown.classList.toggle('open', willOpen);
      dropdownToggle.setAttribute('aria-expanded', String(willOpen));
      return;
    }

    const modalTrigger = event.target.closest('[data-modal-target]');
    if (modalTrigger) {
      showModal(modalTrigger.getAttribute('data-modal-target'));
      return;
    }

    const closeTrigger = event.target.closest('[data-modal-close]');
    if (closeTrigger) {
      hideModal(closeTrigger.closest('.modal'));
      return;
    }

    if (event.target.classList.contains('modal')) {
      hideModal(event.target);
      return;
    }

    if (!event.target.closest('.dropdown')) {
      closeDropdowns();
    }

    if (!event.target.closest('.navbar') || event.target.closest('.navbar-menu .nav-link, .navbar-menu .dropdown-item')) {
      closeMenus();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeMenus();
      closeDropdowns();
      document.querySelectorAll('.modal.show').forEach(hideModal);
    }
  });

  document.addEventListener('change', (event) => {
    if (event.target.closest('#species-form')) {
      event.target.form.submit();
    }
  });
})();
