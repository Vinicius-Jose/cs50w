document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  create_email_view();
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#mail-box').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-box').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  mail_list = document.createElement('div');
  mail_list.setAttribute("id", "mailList");
  mail_list.setAttribute("class", "list-group");
  document.querySelector('#emails-view').append(mail_list);
  const class_unread = 'list-group-item list-group-item-action flex-column align-items-start  font-weight-bold';
  const class_read = 'list-group-item list-group-item-action flex-column align-items-start list-group-item-dark';

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => emails.forEach(email => {
      let link = document.createElement('a');
      let class_link = class_unread;
      if (email.read) {
        class_link = class_read;
      }
      link.setAttribute('class', class_link);
      const email_box = document.createElement('div');
      const sender = document.createElement('h8');
      const email_date = document.createElement('small');
      email_box.setAttribute('class', "d-flex w-100 justify-content-between");
      sender.setAttribute('class', "mb-1 ");

      sender.innerHTML = `${email.sender} -  Subject: ${email.subject}`;
      email_date.innerText = email.timestamp;

      if (mailbox == 'inbox' || mailbox == 'archive') {
        archive_button = document.createElement("button");
        archive_button.setAttribute('id', `archive_button`);
        archive_button.setAttribute('class', 'btn btn-primary btn-sm ml-2');
        archive_button.innerHTML = "archive";
        archive_button.addEventListener('click', (event) => archive_email(event, email.id, !email.archived));
        if (mailbox == 'archive') {
          archive_button.innerHTML = "unarchive";
        }
        email_date.appendChild(archive_button);
      }
      email_box.appendChild(sender);
      email_box.appendChild(email_date);
      link.appendChild(email_box);
      link.addEventListener('click', (event) => {
        if (event.target.id == `archive_button`) {
          event.preventDefault();
        } else {
          view_email(email.id);
        }

      });
      mail_list.appendChild(link);
    }))

}


function send_email(event) {
  recipients = document.querySelector('#compose-recipients').value;
  subject = document.querySelector('#compose-subject').value;
  body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
    .then(response => response.json())
    .then(result => {
      if (result.error) {
        alert(result.error);
      } else {
        load_mailbox('inbox');
      }
    });
  event.preventDefault();
  return false;
}


function view_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })

  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#mail-box').style.display = 'block';


  sender = document.querySelector('#email-sender');
  body = document.querySelector('#email-body');
  subject = document.querySelector('#email-subject');
  recipients = document.querySelector('#email-recipients');
  reply_button = document.createElement("button");
  reply_button.setAttribute('id', `reply_button`);
  reply_button.setAttribute('class', 'btn btn-primary btn-sm ml-2');
  reply_button.innerHTML = "Reply";
  reply_button.addEventListener('click', () => reply(email_id));

  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      let recipient_names = ''
      sender.innerHTML = `From: ${email.sender} - ${email.timestamp}`
      body.innerHTML = email.body
      subject.innerHTML = `Subject:  ${email.subject}`
      email.recipients.forEach(recipient => {
        recipient_names += `${recipient}, `;
      })
      recipients.innerHTML = `To: ${recipient_names}`;
      sender.appendChild(reply_button)

    });



}

function create_email_view() {
  const container = document.querySelector('.container');
  const email_box = document.createElement("div");
  email_box.setAttribute("id", "mail-box");
  email_box.setAttribute("class", "card");
  const sender = document.createElement("div");
  sender.setAttribute("class", "card-header");
  sender.setAttribute("id", "email-sender");
  const recipients = document.createElement("div");
  recipients.setAttribute("class", "card-header");
  recipients.setAttribute("id", "email-recipients");
  const body = document.createElement("div");
  body.setAttribute("class", "card-body");
  body.setAttribute("id", "email-body-box");
  const subject = document.createElement("h5");
  subject.setAttribute("class", "card-title");
  subject.setAttribute("id", "email-subject");
  const email_body = document.createElement("p");
  email_body.setAttribute("class", "card-text");
  email_body.setAttribute("id", "email-body");

  body.appendChild(subject);
  body.appendChild(email_body);
  email_box.appendChild(sender);
  email_box.appendChild(recipients);
  email_box.appendChild(body);
  container.append(email_box);
  view = document.querySelector('#mail-box');
  view.style.display = 'none';
}


function archive_email(event, email_id, archived) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: archived
    })
  }).then(response => load_mailbox('inbox'));


}


function reply(email_id) {
  compose_email();
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      subject = email.subject
      if (!subject.includes("Re:")) {
        subject = `Re: ${subject}`
      }
      body = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`

      document.querySelector('#compose-recipients').value = email.sender

      document.querySelector('#compose-subject').value = subject
      document.querySelector('#compose-body').value = body;

    });
}
