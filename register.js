document.addEventListener('DOMContentLoaded', function() {
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.onsubmit = async function(e) {
      e.preventDefault();
      const username = document.getElementById('registerUsername').value.trim();
      const pwd1 = document.getElementById('registerPwd1').value;
      const pwd2 = document.getElementById('registerPwd2').value;
      const msg = document.getElementById('msg');
      if (!username || !pwd1 || !pwd2) {
        msg.textContent = 'All fields required.';
        return;
      }
      if (pwd1 !== pwd2) {
        msg.textContent = 'Passwords do not match.';
        return;
      }
      // Call backend to register user
      const resp = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contact: username, username: username, password: pwd1, otp: '000000' }) // dummy OTP if not used
      });
      const data = await resp.json();
      if (data.ok) {
        window.location.reload();
      } else {
        msg.textContent = data.error || 'Registration failed.';
      }
    };
  }

  const createAccountForm = document.getElementById('createAccountForm');
  if (createAccountForm) {
    createAccountForm.onsubmit = async function(e) {
      e.preventDefault();
      const username = createAccountForm.username.value.trim();
      const email = createAccountForm.email.value.trim();
      const pwd1 = createAccountForm.password.value;
      const pwd2 = createAccountForm.confirm_password.value;
      if (!username || !email || !pwd1 || !pwd2) {
        alert('All fields required.');
        return;
      }
      if (pwd1 !== pwd2) {
        alert('Passwords do not match.');
        return;
      }
      // Send registration data to backend
      const resp = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password: pwd1 })
      });
      const data = await resp.json();
      if (data.ok) {
        alert('Account created! Please check your email to verify your account.');
        window.location.href = 'signin.html';
      } else {
        alert(data.error || 'Registration failed.');
      }
    };
  }
});
