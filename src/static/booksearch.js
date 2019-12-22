class Booksearch {
  constructor(booksearch_url, form, input, results, selected, loader) {
    this.booksearch_url = booksearch_url;
    this.books = [];
    this.selected = null;
    this.form = form;
    this.input = input;
    this.loader = loader;
    this.results = results;
    this.div = selected;
    this.editing = null;
  }

  searchBooks(query) {
    this.loader.classList.remove("hidden");
    fetch(this.booksearch_url + "?search=" + query).then(data => {
      this.loader.classList.add("hidden");
      data.json().then(results => {
        this.books = results.books;
        this.renderResults();
      });
    });
  }

  bindEventListeners() {
    this.form.addEventListener("submit", evt => {
      evt.preventDefault();
      this.searchBooks(this.input.value);
    });
    this.results.addEventListener("click", evt => {
      if (evt.target) {
        const book = this.books.find(book => book.id === evt.target.id);
        this.selected = book;
        this.books = [];
        this.renderResults();
        this.renderSelected();
      } else {
        console.log("No target on event: " + event);
      }
    });
  }

  renderResults() {
    this.results.innerHTML = "";
    this.books.forEach(result => {
      const li = document.createElement("li");
      li.setAttribute("id", result.id);
      li.classList.add("search-result");

      const thumbnail = document.createElement("div");
      thumbnail.setAttribute("id", result.id);
      thumbnail.classList.add("search-result-thumbnail");

      const img = document.createElement("img");
      img.setAttribute("id", result.id);
      img.setAttribute("src", result.image_url);
      thumbnail.appendChild(img);
      li.appendChild(thumbnail);

      const text = document.createElement("div");
      text.setAttribute("id", result.id);
      text.classList.add("search-result-text");

      const titleHtml = "<span class=\"book-title\" id=\"" + result.id + "\">" + result.title + "</span>";
      if (result.author !== "") {
        text.innerHTML += titleHtml + "<span id=\"" + result.id + "\">&nbsp;&ndash; " + result.author + "</span>";
      } else {
        text.innerHTML += titleHtml;
      }

      var isbnText = ""

      if (result.isbn13 || result.isbn10) {
        text.innerHTML
      }

      if (result.isbn13) {
        isbnText += result.isbn13;
      }

      if (result.isbn10 && result.isbn13) {
        isbnText += " / "
      }

      if (result.isbn10) {
        isbnText += result.isbn10;
      }

      if (isbnText !== "") {
        text.innerHTML+= "<br/><div class=\"isbn\" id=\"" + result.id + "\">" + isbnText + "</div>";
      }

      li.appendChild(text);
      this.results.appendChild(li);
    });
  }

  renderSelected() {
    if (this.selected) {
      this.input.value = "";
      this.div.classList.remove("hidden");

      const bookDisplay = document.createElement("div");
      bookDisplay.classList.add("book-preview")

      const thumbnail = document.createElement("div");
      thumbnail.classList.add("book-thumbnail");
      const img = document.createElement("img");
      img.setAttribute("src", this.selected.image_url);
      thumbnail.appendChild(img);

      if (this.selected.image_url !== "") {
        bookDisplay.appendChild(thumbnail);
      }

      const metadata = document.createElement("div");
      metadata.classList.add("book-metadata")
      metadata.innerHTML = "<span class=\"book-title\">" + this.selected.title + "</span>";

      if (this.selected.year !== "" || this.selected.year != "") {
        metadata.innerHTML += "<br />";

        if (this.selected.author !== "") {
          metadata.innerHTML += this.selected.author;
        }

        if (this.selected.year !== "" && this.selected.year != "") {
          metadata.innerHTML += ", "
        }

        if (this.selected.year !== "") {
          metadata.innerHTML += this.selected.year;
        }
      }
      bookDisplay.appendChild(metadata);

      this.div.querySelector("#info").appendChild(bookDisplay);
      this.div.querySelector("#title").value = this.selected.title;
      this.div.querySelector("#year").value = this.selected.year;
      this.div.querySelector("#author").value = this.selected.author;
      this.div.querySelector("#image_url").value = this.selected.image_url;
      this.div.querySelector("#identifiers").value = this.selected.identifiers;
      this.div.querySelector("#source_id").value = this.selected.id;
    } else {
      this.div.classList.add("hidden");
    }
  }
}

class Books {
  constructor(container) {
    this.container = container;
    this.editing = null;
  }

  addEventListeners() {
    [...document.querySelectorAll(".edit-book")].forEach(item => {
      item.addEventListener("click", evt => {
        if (this.editing === null) {
          this.editing = parseInt(evt.target.dataset["bookid"]);
        } else {
          this.editing = null;
        }
        this.renderEditing();
      });
    });
    [...document.querySelectorAll(".cancel-edit")].forEach(item => {
      item.addEventListener("click", evt => {
        this.editing = null;
        this.renderEditing();
      });
    });
  }

  renderEditing() {
    const div = document.getElementById("book-" + this.editing);

    if (this.editing) {
      console.log(this.editing);
      console.log(div);
      const form = div.querySelector(".book-edit-form");

      form.classList.remove("hidden");
    } else {
      [...document.querySelectorAll(".book-edit-form")].forEach(item => {
        item.classList.add("hidden");
      });
    }
  }
}

class Reading {
  constructor(container) {
    this.container = container;
    this.editing = null;
  }

  addEventListeners() {
    [...document.querySelectorAll(".edit-reading")].forEach(item => {
      item.addEventListener("click", evt => {
        if (this.editing === null) {
          this.editing = parseInt(evt.target.dataset["readingid"]);
        } else {
          this.editing = null;
        }
        this.renderEditing();
      });
    });
    [...document.querySelectorAll(".cancel-edit")].forEach(item => {
      item.addEventListener("click", evt => {
        this.editing = null;
        this.renderEditing();
      });
    });
  }

  renderEditing() {
    console.log(this.editing);
    const div = document.getElementById("reading-" + this.editing);

    console.log(div);

    if (this.editing) {
      const form = div.querySelector(".reading-edit-form");

      form.classList.remove("hidden");
    } else {
      [...document.querySelectorAll(".reading-edit-form")].forEach(item => {
        item.classList.add("hidden");
      });
    }
  }
}

class Plans {
  constructor(container) {
    this.container = container;
    this.editing = null;
  }

  addEventListeners() {
    [...document.querySelectorAll(".edit-plan")].forEach(item => {
      item.addEventListener("click", evt => {
        console.log(evt);
        if (this.editing === null) {
          this.editing = parseInt(evt.target.dataset["planid"]);
          console.log(this.editing);
        } else {
          this.editing = null;
        }
        this.renderEditing();
      });
    });
    [...document.querySelectorAll(".cancel-edit")].forEach(item => {
      item.addEventListener("click", evt => {
        this.editing = null;
        this.renderEditing();
      });
    });
  }

  renderEditing() {
    const div = document.getElementById("plan-" + this.editing);

    if (this.editing) {
      const form = div.querySelector(".plan-edit-form");

      form.classList.remove("hidden");
    } else {
      [...document.querySelectorAll(".plan-edit-form")].forEach(item => {
        item.classList.add("hidden");
      });
    }
  }
}
