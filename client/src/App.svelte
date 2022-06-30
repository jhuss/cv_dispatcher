<script lang="ts">
  import Captcha from './Captcha.svelte';

  let email = undefined;
  let name = undefined;
  let note = undefined;
  let captcha = undefined;
  let refreshCaptcha = undefined;

  let status = '';
  let messages = [];
  $: notificationLevel = '';

  function notificationClass() {
    switch (status) {
      case 'ERROR':
      case 'CAPTCHA-EXPIRED':
        return 'is-danger';
      case 'EXIST':
        return 'is-warning';
      case 'CREATED':
      case 'FORWARDED':
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

  function requestForCv(event, forward=false) {
    const bodyData = {
      address: cleanInput(email),
      name: cleanInput(name),
      note: cleanInput(note),
      captcha: cleanInput(captcha)
    }

    if (forward) {
      bodyData['forward'] = true;
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

      if (['CAPTCHA-EXPIRED', 'CREATED', 'FORWARDED'].includes(status)) {
        refreshCaptcha();
      }
    });
  }

  function forwardRequest(event) {
    requestForCv(event, true);
  }
</script>

<svelte:head>
  <style src="./style/main.scss"></style>
</svelte:head>

<div class="container">
  <div class="columns is-centered">
    <div class="column is-half">
      <section class="section">
        <h3 class="title has-text-centered">__HEADER__</h3>
        <h5 class="subtitle has-text-centered">__DESCRIPTION__</h5>
      </section>

      <form class="box">
        <div class="field mb-4">
          <div class="control">
            <p class="subtitle is-5 has-text-centered">Please complete the form to receive the CV download by email.</p>
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
                <br/><button on:click|preventDefault={forwardRequest} class="button is-info">Click to forward CV</button>
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

        <div class="field">
          <label class="label" for="captcha-field">Captcha</label>
          <div class="control">
            <Captcha bind:captcha={captcha} bind:refreshCaptcha={refreshCaptcha}/>
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
