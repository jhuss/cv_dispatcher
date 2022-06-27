<script lang="ts">
  let email = undefined;
  let name = undefined;
  let note = undefined;

  let status = '';
  let messages = [];
  $: notificationLevel = '';

  function notificationClass() {
    switch (status) {
      case 'ERROR':
        return 'is-danger';
      case 'EXIST':
        return 'is-warning';
      case 'CREATED':
        return 'is-success';
      default:
        return 'is-info';
    }
  }

  function cleanInput(inputValue) {
    switch (typeof inputValue) {
      case 'string':
        let value = String(inputValue).trim();
        return (value === '') ? undefined : value;
      default:
        return inputValue;
    }
  }

  function requestForCv(event) {
    const bodyData = {
      address: cleanInput(email),
      name: cleanInput(name),
      note: cleanInput(note)
    }

    fetch('__SERVER__/petition', {
      method: 'post',
      mode: 'cors',
      body: JSON.stringify(bodyData)
    })
    .then(response => response.json())
    .then((data) => {
      status = data.status;
      messages = data.messages;
      notificationLevel = notificationClass();
    });
  }

  function resendRequest() {
    // TODO: implement
    console.log('resend!');
  }
</script>

<svelte:head>
  <style src="./style/main.scss"></style>
</svelte:head>

<div class="container">
  <div class="columns is-centered">
    <div class="column is-half">
      <section class="section">
        <div class="content">
          <p class="title is-3 has-text-centered">Jesus Jerez CV Download</p>
        </div>
      </section>

      <form class="box">
        <div class="field mb-4">
          <div class="control">
            <p class="subtitle is-5 has-text-centered">Please, provide the email address to receive the CV download</p>
          </div>
        </div>

        {#if status !== ''}
        <div class="field">
          <div class="notification {notificationLevel}">
            <ul>
            {#each messages as message, i}
              <li>{message}.</li>
            {/each}
            {#if status === 'EXIST'}
              <li>
                <br/><button on:click|preventDefault={resendRequest} class="button is-info">Click to resend CV</button>
              </li>
            {/if}
            </ul>
          </div>
        </div>
        {/if}

        <div class="field">
          <label class="label" for="email-field">Email</label>
          <div class="control has-icons-left">
            <input bind:value={email} id="email-field" class="input" type="email">
            <span class="icon is-small is-left">
              <i class="fas fa-envelope"></i>
            </span>
          </div>
        </div>

        <div class="field">
          <label class="label" for="name-field">Name or Company</label>
          <div class="control has-icons-left">
            <input bind:value={name} id="name-field" class="input" type="text">
            <span class="icon is-small is-left">
              <i class="fas fa-building-user"></i>
            </span>
          </div>
        </div>

        <div class="field">
          <label class="label" for="note-field">Note (optional)</label>
          <div class="control">
            <textarea bind:value={note} id="note-field" class="textarea"></textarea>
          </div>
        </div>

        <div class="field is-grouped is-grouped-right">
          <div class="control">
            <button on:click|preventDefault={requestForCv} class="button is-info">Click to request CV</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</div>

<style lang="scss">
</style>
