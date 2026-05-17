$(function () {
  const $form = $('#message-form');
  const $name = $('#name');
  const $content = $('#content');
  const $submit = $('#submit-button');
  const $feedback = $('#feedback');
  const $messageList = $('#message-list');
  const $refresh = $('#refresh-button');

  function escapeHtml(value) {
    return $('<div>').text(value == null ? '' : String(value)).html();
  }

  function showFeedback(message, type) {
    $feedback
      .removeClass('feedback--success feedback--error')
      .addClass(type === 'success' ? 'feedback--success' : 'feedback--error')
      .text(message || '');
  }

  function clearFeedback() {
    $feedback
      .removeClass('feedback--success feedback--error')
      .text('');
  }

  function setSubmitting(isSubmitting) {
    $submit.prop('disabled', isSubmitting);
    $submit.text(isSubmitting ? '送出中...' : '送出留言');
  }

  function renderMessages(messages) {
    if (!Array.isArray(messages) || messages.length === 0) {
      $messageList.html('<p class="empty-state">目前還沒有留言，來當第一位留言的人吧！</p>');
      return;
    }

    const html = messages.map(function (message) {
      const name = escapeHtml(message.name || '匿名');
      const content = escapeHtml(message.content || '').replace(/\n/g, '<br>');
      const createdAt = escapeHtml(message.created_at || '');

      return `
        <article class="message-card">
          <div class="message-card__meta">
            <strong class="message-card__name">${name}</strong>
            <time class="message-card__time">${createdAt}</time>
          </div>
          <p class="message-card__content">${content}</p>
        </article>
      `;
    }).join('');

    $messageList.html(html);
  }

  function loadMessages() {
    $messageList.addClass('message-list--loading');

    return $.ajax({
      url: 'api/list.php',
      method: 'GET',
      dataType: 'json'
    }).done(function (response) {
      if (response && response.success) {
        renderMessages(response.messages || []);
      } else {
        renderMessages([]);
        showFeedback((response && response.error) || '讀取留言失敗。', 'error');
      }
    }).fail(function () {
      renderMessages([]);
      showFeedback('無法連線到留言列表 API，請確認 XAMPP 與資料庫是否已啟動。', 'error');
    }).always(function () {
      $messageList.removeClass('message-list--loading');
    });
  }

  $form.on('submit', function (event) {
    event.preventDefault();
    clearFeedback();

    const name = $.trim($name.val());
    const content = $.trim($content.val());

    if (!name) {
      showFeedback('請輸入暱稱。', 'error');
      $name.trigger('focus');
      return;
    }

    if (!content) {
      showFeedback('請輸入留言內容。', 'error');
      $content.trigger('focus');
      return;
    }

    setSubmitting(true);

    $.ajax({
      url: 'api/create.php',
      method: 'POST',
      dataType: 'json',
      data: {
        name: name,
        content: content
      }
    }).done(function (response) {
      if (response && response.success) {
        $content.val('');
        showFeedback('留言已送出。', 'success');
        loadMessages();
      } else {
        showFeedback((response && response.error) || '新增留言失敗。', 'error');
      }
    }).fail(function (xhr) {
      const response = xhr.responseJSON;
      showFeedback((response && response.error) || '無法新增留言，請稍後再試。', 'error');
    }).always(function () {
      setSubmitting(false);
    });
  });

  $refresh.on('click', function () {
    clearFeedback();
    loadMessages();
  });

  loadMessages();
});
