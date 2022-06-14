<script lang="ts">
  let email = '';

  function requestForCv(event) {
    console.log("send cv to:", email);

    fetch('http://localhost:8000/petition', {
      method: 'post',
      mode: 'cors',
      body: JSON.stringify({
        address: email
      })
    });
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

        <div class="field">
          <label class="label" for="email-field">Email</label>
          <div class="control has-icons-left">
            <input bind:value={email} id="email-field" class="input" type="email" placeholder="e.g. me@domain.com">
            <span class="icon is-small is-left">
              <i class="fas fa-envelope"></i>
            </span>
          </div>
        </div>

        <div class="field is-grouped is-grouped-right">
          <div class="control">
            <button on:click|preventDefault={requestForCv} class="button is-info">Request CV</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</div>

<style lang="scss">
</style>
