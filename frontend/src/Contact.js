import React from 'react';
import './Contact.css';

function Contact() {
    return (
        <div className="contact">
            <p className="contact-text">
                Thank you for taking a look at my work! Please feel free to contact me at&nbsp;
                <a className="email" href="mailto:leo7deng@gmail.com">leo7deng@gmail.com</a>
                . <br></br>You may also view my other projects here!
                {/* <a href=" */}
            </p>

        </div>
    );
}

export default Contact;