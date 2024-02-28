import React from 'react';
import './Contact.css';

function Contact() {
    return (
        <div className="contact">
            <p className="contact-text">
                Thank you for taking a look at my work! <br></br>You can view the source code for this project on my&nbsp;
                <a className="github" href="https://github.com/Leo7Deng/SpotifySifter">GitHub</a> <br></br>
                Please feel free to contact me at&nbsp;
                <a className="email" href="mailto:leo7deng@gmail.com">leo7deng@gmail.com</a>
                . <br></br>You may also view my other projects <a href="https://leodeng.com">here</a>!
            </p>

        </div>
    );
}

export default Contact;